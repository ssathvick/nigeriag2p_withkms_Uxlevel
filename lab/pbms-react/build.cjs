const esbuild=require('esbuild');
const fs=require('node:fs');
fs.mkdirSync('dist',{recursive:true});
esbuild.buildSync({entryPoints:['src/main.jsx'],outfile:'dist/app.js',bundle:true,minify:true,target:['es2020'],define:{'process.env.NODE_ENV':'"production"'}});
fs.copyFileSync('index.html','dist/index.html');
