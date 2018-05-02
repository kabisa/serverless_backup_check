
test:
	@./tests/test.sh

ci:
	@docker build . --tag backup && docker run -t backup

clean:
	@find . -type d | grep "pycache" | xargs rm -r
	@rm -rf htmlcov

deploy:
	./deploy.sh

.PHONY: test ci clean deploy

