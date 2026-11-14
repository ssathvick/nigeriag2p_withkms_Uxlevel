require('esbuild').buildSync({entryPoints:['src/shell.js'],outfile:'dist/site-shell.js',bundle:true,minify:true,target:['es2020']});
