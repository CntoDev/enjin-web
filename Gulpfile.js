var path = require("path"),
    _ = require("lodash"),
    webserver = require("gulp-webserver"),
    sequence = require("run-sequence"),
    fileinclude = require("gulp-file-include"),
    gulp = require("gulp"),
    sass = require("gulp-sass"),
    clean = require("gulp-clean"),
    source = require("vinyl-source-stream"),
    gutil = require("gulp-util"),
    sourcemaps = require("gulp-sourcemaps"),
    watchify = require("watchify"),
    browserify = require("browserify"),
    livereload = require("gulp-livereload"),

    mappedPaths = {
      'styles': 'styles',
      'dist': 'dist'
    },

    options = {
      env: process.env.NODE_ENV,
      sourcemaps: false,
      minify: false,
      watch: false,
      debug: false
    };

gulp.task("dist", function(done) {
  options.env = options.env || "production";
  options.minify = true;

  return sequence(
    "clean",
    ["styles", "scripts", "html", "images"],
    done
  );
});

gulp.task("build", function(done) {
  return sequence(
    "clean",
    ["styles", "scripts", "html", "images"],
    "watch",
    done
  );
});

gulp.task("server", ["build"], function(done) {
  return gulp.src(dir("dist")).pipe(webserver({
    livereload: true,
    port: 3000
  }));
});

gulp.task("watch", function() {
//  livereload.listen();

  gulp.watch(dir("styles", "**/*.{sass,scss}"), ["styles"]);
  gulp.watch(dir("html", "**/*.html"), ["html"]);
  //gulp.watch(dir("dist", "**/*")).on("change", livereload.changed);
});

gulp.task("clean", function() {
  return gulp.src(dir("dist"), { read: false }).pipe(clean());
});

gulp.task("images", function() {
  return gulp.src(dir("styles/images/**/*")).pipe(gulp.dest(dir("dist", "styles/images")));
});

gulp.task('styles', buildStyles);
gulp.task("scripts", buildScripts);
gulp.task("html", function() {
  return gulp.src("./html/**/*.html")
             .pipe(fileinclude({
               prefix: "@@"
             }))
             .pipe(gulp.dest(dir("dist")));
});

function buildScripts() {
  var bundler,
      entryPoint = "./scripts/cnto.js",

      bundlerOptions = {
        basedir: __dirname,
        debug: options.debug,
        extensions: [".js"],
        // needed for watchify
        cache: {},
        packageCache: {},
        fullPaths: true
      };

  bundler = browserify(entryPoint, bundlerOptions);

  if (options.watch) {
    bundler = watchify(bundler);
    bundler.on("update", makeBundle);
  }

  function makeBundle() {
    var bundle = bundler.bundle();

    return bundle.on("error", handleError("browserify"))
                 .pipe(source("scripts/cnto.js"))
                 .pipe(gulp.dest(dir("dist")));

  }

  return makeBundle();
}

function buildStyles() {
  var srcDir = dir('styles', 'cnto.scss'),
      destDir = dir('dist', 'styles'),
      sassOptions = {
        errLogToConsole: true
      },
      sourcemapsInit = options.sourcemaps ? sourcemaps.init() : gutil.noop();
      sourcemapsWrite = options.sourcemaps ? sourcemaps.write() : gutil.noop();

  sassOptions.outputStyle = options.minify ? "compressed" : "nested";
  sassOptions.errLogToConsole = !!options.watch;

  return  gulp.src(srcDir)
              .pipe(sourcemapsInit)
              .pipe(sass(sassOptions))
              .on("error", handleError("sass"))
              .pipe(sourcemapsWrite)
              .pipe(gulp.dest(destDir));
}

function dir(root) {
  var args = _.toArray(arguments);
  args[0] = mappedPaths[root] || root;
  return path.join.apply(path, args);
}

function handleError(errSection) {
  return function(err) {
    gutil.log(gutil.colors.bgRed(errSection), err);
    this.emit("end");
  };
}


