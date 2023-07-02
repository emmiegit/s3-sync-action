# GitHub Action to Sync S3 Bucket 🔄

This is a fork of [jakejarvis/s3-sync-action](https://github.com/jakejarvis/s3-sync-action) which works around an issue with aws-cli applying an incorrect charset in MIME guessing mode. Due to how long outstanding this issue is, it seems unlikely it will be fixed. See https://github.com/aws/aws-cli/issues/1346.

This action is based on the above, but does not invoke aws-cli, instead using its own system to sync the source and destination directory. As such, it lacks several options found in the parent GitHub workflow action. The intended use case is uploading built files to a destination subdirectory in S3, replacing any existing contents.


## Usage

### Options

* `--delete` **permanently deletes** files in the S3 bucket under `DEST_DIR` which are **not** present in your latest build.
* `--exclude <dir>` skips the given directory when scanning.

### `workflow.yaml` Example

Place in a `.yaml` file such as this one in your `.github/workflows` folder. [Refer to the documentation on workflow YAML syntax here](https://help.github.com/en/articles/workflow-syntax-for-github-actions).

```yaml
name: Upload Website

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v1
    - uses: emmiegit/s3-sync-action@main
      with:
        args: --delete
      env:
        AWS_S3_BUCKET: ${{ secrets.AWS_S3_BUCKET }}
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        AWS_REGION: 'us-east-2'
        SOURCE_DIR: 'public'      # optional: defaults to entire repository
        DEST_DIR: 'blog'          # optional: defaults to root of bucket
```


### Configuration

The following settings must be passed as environment variables as shown in the example. Sensitive information, especially `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, should be [set as encrypted secrets](https://help.github.com/en/articles/virtual-environments-for-github-actions#creating-and-using-secrets-encrypted-variables) — otherwise, they'll be public to anyone browsing your repository's source code and CI logs.

| Key | Value | Suggested Type | Required | Default |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| `AWS_ACCESS_KEY_ID` | Your AWS Access Key. [More info here.](https://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html) | `secret env` | **Yes** | N/A |
| `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Access Key. [More info here.](https://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html) | `secret env` | **Yes** | N/A |
| `AWS_S3_BUCKET` | The name of the bucket you're syncing to. For example, `jarv.is` or `my-app-releases`. | `secret env` | **Yes** | N/A |
| `AWS_REGION` | The region where you created your bucket. Set to `us-east-1` by default. [Full list of regions here.](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions) | `env` | **Yes** | N/A |
| `AWS_S3_ENDPOINT` | The endpoint URL of the bucket you're syncing to. Can be used for [VPC scenarios](https://aws.amazon.com/blogs/aws/new-vpc-endpoint-for-amazon-s3/) or for non-AWS services using the S3 API, like [DigitalOcean Spaces](https://www.digitalocean.com/community/tools/adapting-an-existing-aws-s3-application-to-digitalocean-spaces). | `env` | No | Automatic (`s3.amazonaws.com` or AWS's region-specific equivalent) |
| `SOURCE_DIR` | The local directory (or file) you wish to sync/upload to S3. For example, `public`. Defaults to your entire repository. | `env` | No | `./` (root of cloned repository) |
| `DEST_DIR` | The directory inside of the S3 bucket you wish to sync/upload to. For example, `my_project/assets`. Defaults to the root of the bucket. | `env` | No | `/` (root of bucket) |


## License

This project is distributed under the [MIT license](LICENSE.md).
