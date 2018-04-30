
test:
	./tests/test.sh

ci:
	docker build . --tag backup && docker run -t backup

.PHONY: test ci

