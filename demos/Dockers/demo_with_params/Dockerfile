FROM python:2-onbuild

USER root


COPY push_policy.py /src/push_policy.py
COPY policy.json /src/policy.json
CMD ["python","/src/push_policy.py"]

