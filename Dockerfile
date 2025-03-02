FROM python:3.11-slim

COPY ./log_processor /log_processor

ENTRYPOINT ["python", "/log_processor/log_processor.py"]
