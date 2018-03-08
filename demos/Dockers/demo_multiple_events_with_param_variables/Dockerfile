FROM python:2-onbuild

USER root


COPY push_policy_multiple_events_params.py /src/push_policy_multiple_events_params.py
COPY policy.json /src/policy.json
CMD ["python","/src/push_policy_multiple_events_params.py"]

