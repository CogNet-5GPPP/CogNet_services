FROM python:2-onbuild

USER root


COPY ml_multiple_params.py /src/ml_multiple_params.py
COPY policy.json /src/policy.json
CMD ["python","/src/ml_multiple_params.py"]