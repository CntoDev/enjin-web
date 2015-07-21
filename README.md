# CNTO web development and script repository

Our CSS and JS are generated using [Gulp](http://gulpjs.com/) and [Sass](http://sass-lang.com/).

# Web development environment

## Windows

1. Install gulp by following [these](http://omcfarlane.co.uk/install-gulp-js-windows/) instructions.  Only steps one and two will be necessary as the project is already setup in the root directory of the repo in the gulpfile.js and package.json files.
2. If everything was set up correctly, you will be able to start your local webserver with: ```gulp server```
3. By default, the server will be at [http://localhost:3000](http://localhost:3000) and you can view each of the configured pages that use the generated CSS and static html (found in the repo under /html) on pages such as [http://localhost:3000/roster.html](http://localhost:3000/roster.html).  This page will refresh automatically as the appropriate SCSS files are changed.
4. Once you are happy with your changes you can generate the final minified stuff using:```gulp dist``` This will generate everything you need into the /dist directory.
5. Upload files from the /dist directory to the production server as appropriate! Good work!
