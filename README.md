# Disturbed CLI

Simple CLI that update users in Slack user groups based on OpsGenie on-call schedules.

> Note: It's intended to be run as a cron job.

## Configuration

### Environment variables
- `DISTURBED_OPSGENIE_API_KEY`: API key used to fetch schedules in OpsGenie.
  - It needs `Read` and `Configuration Access` access rights.
  - You can read this [page](https://support.atlassian.com/opsgenie/docs/api-key-management/) to learn how to create an API key.
- `DISTURBED_SLACK_API_TOKEN`: Bot Token used to fetch users, user groups and update use groups.
  - It needs `users:read`, `users:read.email`, `usergroups:read` and `usergroups:write` scopes.
  - You can read this [page](https://api.slack.com/tutorials/tracks/getting-a-token) to quickly get a Slack Bot Token.
  - Remember to review your workspace permissions for User Groups. It must allow users to update user groups (for more details, [see](https://api.slack.com/methods/usergroups.users.update#markdown)).
- `DISTURBED_CONFIG_FILE` [not required]: Path to the configuration file. Defaults to `config.yaml`.
- `DISTURBED_LOG_LEVEL` [not required]: Logging level to use in the project.
  - It's based on [Python's logging levels](https://docs.python.org/3/library/logging.html#logging-levels).

### Configuration file

```yaml
schedules_mapping:
    # Schedule name in OpsGenie to fetch who's on-call.
  - schedule_name: ''
    # User group name in Slack to be updated based on the OpsGenie schedule.
    user_group_name: ''

    # Optional. Overrides OpsGenie schedules based on the given config.
    overrides:
        # Email of the user that's on-call.
      - user_email: ''
        # Current time (in the given timezone) must be within the given time range. Format: HH:MM:SS.
        timezone: ''
        starts_on: ''
        ends_on: ''
        # Optional. Defaults to all_days.
        # Days that should be considered to override. Possible values:
        # - all_days
        # - weekdays
        # - weekends
        repeats_on: ''
        # Update the user group in Slack with the given users instead of the one that's on-call.
        replace_by:
          - ''
```

**Example**

<details open>
<summary>config.yaml</summary>

```yaml
schedules_mapping:
  - schedule_name: product
    user_group_name: 'product-oncall'
  - schedule_name: sre
    user_group_name: 'sre-oncall'
    overrides:
      - user_email: john.doe@gmail.com
        timezone: 'America/Fortaleza'
        starts_on: '23:00:00'
        ends_on: '01:00:00'
        repeats_on: weekdays
        replace_by:
          - jane.doe@gmail.com
```
</details>

### Docker image

There is a Docker image you can use to run this project.

e.g.,

```bash
docker run \
  -e DISTURBED_OPSGENIE_API_KEY='<api-key>' \
  -e DISTURBED_SLACK_API_TOKEN='<bot-token>' \
  -v ./config.yaml:/app/config.yaml \
  ghcr.io/hpedrorodrigues/disturbed_cli:<version>
```

### Helm chart

Helm chart is available [here](https://github.com/hpedrorodrigues/helm-charts/tree/main/charts/disturbed-cli).
