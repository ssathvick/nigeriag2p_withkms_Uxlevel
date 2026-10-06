"""Standalone UI and knowledge service. Never connects to beneficiary databases."""
import hmac,json,os,secrets,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask,g,request,abort,session,render_template,jsonify
import knowledge_management

ROOT=Path(__file__).parent

class KnowledgeConnection(sqlite3.Connection):
    def __exit__(self,*args):
        try:return super().__exit__(*args)
        finally:self.close()

def create_app(config_path=None,database_path=None):
    config=json.loads(Path(config_path or os.environ.get('EXPERIENCE_CONFIG',ROOT/'config/deployment.json')).read_text())
    prefix=config['prefix'].rstrip('/')
    if not prefix.startswith('/') or any(c in prefix for c in ['?','#','<','>']):raise ValueError('prefix must be a URL path')
    for service in config['services']:
        url=service['url'];parsed=urlparse(url)
        if not (url.startswith('/') and not url.startswith('//')) and not (parsed.scheme=='https' and parsed.netloc and not parsed.username):raise ValueError('Service URLs must be relative paths or HTTPS URLs')
    app=Flask(__name__,static_url_path=prefix+'/static')
    app.secret_key=os.environ.get('EXPERIENCE_SESSION_SECRET') or secrets.token_hex(32)
    app.config.update(EXPERIENCE=config,MAX_CONTENT_LENGTH=100000,SESSION_COOKIE_NAME='openg2p-experience',SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=os.environ.get('EXPERIENCE_SECURE_COOKIE','1')!='0',SESSION_COOKIE_PATH=prefix or '/')
    database=Path(database_path or os.environ.get('EXPERIENCE_DATABASE',ROOT/'data/knowledge.sqlite'))
    database.parent.mkdir(parents=True,exist_ok=True)
    gateway_secret=os.environ.get('EXPERIENCE_GATEWAY_SECRET','')

    class Adapter:
        PREFIX=prefix
        def __init__(self):self.app=app;self.config=config
        def db(self):
            c=sqlite3.connect(database,timeout=15,factory=KnowledgeConnection);c.row_factory=sqlite3.Row;return c
        def rows(self,sql,args=()):
            with self.db() as c:return [dict(row) for row in c.execute(sql,args)]
        def one(self,sql,args=()):
            rows=self.rows(sql,args);return rows[0] if rows else None
        def stamp(self):return datetime.now(timezone.utc).isoformat()
        def require_user(self):
            if not g.user:abort(401,'Sign in through the configured identity gateway.')
        def page(self,name,**values):return render_template(name,brand=config['brand']['name'],prefix=prefix,user=g.user,csrf=session['csrf'],**values)
    adapter=Adapter()

    @app.before_request
    def identity_and_csrf():
        g.user=None;g.staff=False;g.session={'mode':'public'}
        token=request.headers.get('X-Experience-Gateway','')
        if gateway_secret and token and hmac.compare_digest(token,gateway_secret):
            sub=request.headers.get('X-Experience-Subject','').strip()
            roles=[r.strip() for r in request.headers.get('X-Experience-Roles','').split(',') if r.strip()]
            if sub:g.user={'sub':sub,'name':request.headers.get('X-Experience-Name',sub),'roles':roles};g.session={'mode':'staff'}
        subject=g.user['sub'] if g.user else None
        if session.get('subject')!=subject:session.clear();session['subject']=subject
        if 'csrf' not in session:session['csrf']=secrets.token_urlsafe(32)
        if request.method in ['POST','PUT','PATCH','DELETE']:
            supplied=request.form.get('csrf','')
            if not supplied or not hmac.compare_digest(supplied,session['csrf']):abort(403,'Invalid CSRF token')

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='same-origin'
        if '/knowledge/admin' in request.path:response.headers['Cache-Control']='no-store'
        return response

    @app.get(prefix+'/health')
    def health():return {'status':'ok','component':'experience-layer'}

    @app.get(prefix+'/')
    def home():return adapter.page('home.html')

    @app.get(prefix+'/api/config')
    def public_config():return jsonify({k:config[k] for k in ['prefix','brand','personas','services']})

    @app.get(prefix+'/embed/config.js')
    def embed_config():
        payload={'baseUrl':config['public_base_url'].rstrip('/'),'knowledgeUrl':config['public_base_url'].rstrip('/')+'/api/knowledge','screenMappings':config['screen_mappings'],'brand':config['brand'],'personas':config['personas']}
        return app.response_class('window.OpenG2PExperience='+json.dumps(payload)+';',mimetype='application/javascript')

    with app.app_context():knowledge_management.install(adapter)
    app.extensions['experience_adapter']=adapter
    return app

app=create_app()
if __name__=='__main__':app.run(host='127.0.0.1',port=int(os.environ.get('PORT','18110')),debug=False)
