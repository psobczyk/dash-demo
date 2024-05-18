## Example of dash app project

This is a dash app written as an example for the classes at the Adam Mickiewicz University.

### How to run the app?

```bash
python3 src/app.py
```

and visit http://127.0.0.1:8050/ in your web browser.

### Building and running basic app docker

```bash
make docker-build

make docker-run
```

### Running redis based app with Docker

```bash
docker-compose build
docker-compose up
# or
make docker-run-compose
```

Cleanup

```bash
docker-compose down
```

### How to contribute

Before commiting make sure that your code passes black and pylint checks.
