NPM_BIN=./node_modules/.bin
LOG_PARSER=| $(NPM_BIN)/bunyan

build: configure
	$(NPM_BIN)/gulp build

dist: configure
	$(NPM_BIN)/gulp dist

server:
	$(NPM_BIN)/gulp server

deploy:
	$(NPM_BIN)/nodemon index.js --env=development $(LOG_PARSER)

clean:
	rm -rf ./dist

.PHONY: dist build deploy clean
