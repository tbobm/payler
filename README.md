# Payl[oad Spoo]ler

_Send your payload now, treat it later._

## What is this?

Payler is an asyncio-based Python application intended to provide a way of delaying message execution. The goal of this program is to reduce the workload on your existing message broker solution (Only RabbitMQ is currently supported, but other message-brokers can be easily implemented) by putting the payloads in a storage backend which will then be polled to re-inject payloads in the corresponding destination.

## Installation

Through pypi:
```console
$ pip install payler
```

Through [poetry](https://github.com/python-poetry/poetry):
```console
$ git clone https://github.com/tbobm/payler
$ cd payler
$ poetry install
```

## How to use this

Using the command line:

1. Specify the input and output URLs for your drivers (see [configuration](#configuration))
2. (optional) Customize the configuration to suit your needs _currently the example configuration is the only valid one_
3. Run payler `payler --config-file configuration.yaml`

Using the docker image:

1. Pull the docker image `docker pull ghcr.io/tbobm/payler:latest`
2. (optional) Customize the configuration to suit your needs _currently the example configuration is the only valid one_ (mount the configuration file into the volume at `/configuration.yaml`)
3. Run the docker image and provide environment variables `docker run -d --name payler -e BROKER_URL="amqp://payler:secret@my-broker/" -e MONGODB_URL="mongodb://payler:secret@my-mongo/payler" ghcr.io/tbobm/payler`

## Configuration

In order to configure the different workflows, payler uses a configuration file (see [configuration.yml](./configuration.yml)).

Example config file:

```yaml
---
workflows:
  - name: "Fetch payloads from RabbitMQ and store them in MongoDB"
    location: "payler"
    callable: "client.process_queue"
  - name: "Re-injects payloads to RabbitMQ"
    callable: "client.watch_storage"
```

The `workflows[].name` attribute is currently unused, but will offer a more human-friendly way of getting informed about a workflow's state.
The `workflows[].location` corresponds to the package where the `workflows[].callable` can be found. It defaults to `payler`, but can this is a way of offering a dumb and simple plugin mechanism by creating function matching the following signature:

```python
async def my_workflow(loop: asyncio.AbstractEventLoop) -> None:
    """My user-defined workflow."""
    # configure your driver(s)
    input_driver.serve()
```

## Features

- Listen to a Broker Queue
- Store messages with a duration or date as metadata
- Re-inject the messages after the duration in the default Exchange
- Output failed messages to global output

## Testing

This project has unittests with [pytest](https://docs.pytest.org/en/latest/). A wrapper script is available at [run-tests.sh](./run-tests.sh).

## Contributing

Feel free to open new issues for feature requests and bug reports in the [issue page](github.com/tbobm/payler/issues/new) and even create PRs if you feel like it.

This project is linted with `pylint` with some minor adjustments (see the [setup.cfg](./setup.cfg)).

## Note

This side-project is born from the following:
- I wanted to experiment with Python's `asyncio`
- A friend of mine had issues with delaying lots of messages using RabbitMQ's [delayed exchange plugin](https://github.com/rabbitmq/rabbitmq-delayed-message-exchange)
- I was looking for a concrete use-case to work with Github Actions.
