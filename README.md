# SuperLesson

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

## Setup

SuperLesson (SL) uses [WhisperX](hhttps://github.com/m-bain/whisperX) through [Replicate](https://replicate.com) to transcribe audio.
SL also uses ChatGPT to improve transcriptions.

In order to access those services, the following keys are needed:
```raw
OPENAI_API_KEY=<your_token>
REPLICATE_API_TOKEN=<your_token>
```

In order to use Replicate, you must also [set up AWS credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration) for putting the audio file into a
bucket.
This is necessary as Replicate will only take direct uploads of very small files.

To set your API keys, you can either pass them by environment variables, or put them in a `.env`
file at the root of the repository.

If you don't want to use Replicate, you can use `--local` flag to transcribe with [faster-whisper](https://github.com/guillaumekln/faster-whisper).
Please check [the section on CUDA](#cuda-support) to learn more about GPU support.

> Note that this may cause worse results, as faster-whisper doesn't support word level alignment.

### Dependencies

Install [poetry](https://python-poetry.org/) and run `poetry install` in order to install
all the dependencies. Keep in mind that as the project is updated you should run have to run it
again.

### Lesson files

Each lesson should have at least a video file, and optionally a PDF for annotations. So for
example:

```raw
lessons/
├── biology-1/
│   ├── video.mp4
│   └── presentation.pdf
└── physics-2/
    └── lecture-2.mp4
```

## Running

> ⚠️ In order to run the `enumerate` step, SL needs to be run in a terminal that supports the [Kitty
> graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/).

To run SL execute

```sh
poetry run superlesson [lesson-id]
```

> A list of options is available through `poetry run superlesson --help`

This will execute all the following steps:

1. `transcribe`
2. `merge` segments using transition frames
3. `enumerate` slides from tframes
4. `replace` known bogus words
5. `improve` punctuation using ChatGPT
6. `annotate` the presentation

You can also run individual steps using

```bash
poetry run [step]
```

> Note: step names are highlighted above using monospace.

### CUDA Support

Transcriptions can be run faster on GPU.
If you have an Nvidia GPU available, the transcription step can be run within a docker environment
with CUDA by passing the `--with-docker` flag.

If you prefer to run without a container, check out instructions on the [faster-whisper docs](https://github.com/guillaumekln/faster-whisper#gpu).

### Comparing steps

If you think some step is misbehaving, or would simply like to see what is happening, you can use
the `--diff` flag followed by the two steps you want to compare, e.g.:

```
poetry run superlesson LESSON --diff merge improve
```

Note that only steps that generate some text output may be used.

For this step you should install [wdiff](https://www.gnu.org/software/wdiff/). 

## Development

First, install `pre-commit`, then run `pre-commit install` to install all the
necessary hooks.

To test the project, run

```bash
poetry run pytest
```

## Troubleshooting

### I don't have a suitable python installed, how do I run?

You can use `pyenv` to manage python versions. After you've installed `pyenv`, run

```bash
$ pyenv install 3.10.11
$ pyenv local 3.10.11
$ poetry env use $(which python3)
```
