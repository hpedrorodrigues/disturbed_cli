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
  - schedule_name: "Schedule name in OpsGenie to fetch who's on-call"
    user_group_name: "User group name in Slack to be updated"
```

**Example**

<details open>
<summary>config.yaml</summary>

```yaml
schedules_mapping:
  - schedule_name: 'SRE'
    user_group_name: 'sre-oncall'
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
