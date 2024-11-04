.PHONY: build deploy pull

build:
		docker build --rm -t my/test_furiganizer:stable .


run:
		docker run -it \
		-v $(PWD):/workdir \
		my/test_furiganizer:stable
