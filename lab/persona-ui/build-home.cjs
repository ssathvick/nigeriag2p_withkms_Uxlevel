require('esbuild').buildSync({entryPoints:['src/site.jsx'],outfile:'dist/site.js',bundle:true,minify:true,define:{'process.env.NODE_ENV':JSON.stringify('production')},target:['es2020']});
