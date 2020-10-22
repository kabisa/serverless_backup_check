
test:
	@./tests/test.sh

ci:
	@docker build . --tag backup && docker run -t backup

clean:
	@find . -type d | grep "pycache" | xargs rm -r
	@rm -rf htmlcov

deploy:
	sls deploy

.PHONY: test ci clean deploy

