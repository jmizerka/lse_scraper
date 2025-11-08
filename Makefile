SRC := app
TESTS := tests

format:
	@echo "Formatting code with Black..."
	black $(SRC) $(TESTS)
lint:
	@echo "Running Flake8..."
	flake8 $(SRC) $(TESTS)
	@echo "Running Pylint..."
	pylint $(SRC)
