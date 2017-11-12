# serverless-feed-logger

This is a simple [AWS Lambda](https://aws.amazon.com/lambda/) function that downloads a file from a given URL and stores logs it to the standard [CloudWatch](https://aws.amazon.com/cloudwatch/) log used by the Lambda function. This is useful if you encounter some frequently changing data on the web, in a small textual format. For example, you may wish to keep snapshots of an XML or JSON feed, such as an ATOM feed from a blog or data from a realtime API. Using Lambda absolves you of having to keep a server on-line for this task. With the help of CloudWatch Events, your function can automatically run on a regular basis, either at a fixed rate (e.g. minutely, hourly, daily), or per a cron expression (e.g. every Sunday at 12:00, the first day of every month at midnight).

This tool is most suitable for small, text-based responses, where the benefits of being able to quickly filter and retrieve results via CloudWatch logs make sense. If the data you want to download is in the hundreds of kilobytes or larger, you are likely better off with my similar [serverless-file-archiver](https://github.com/ranek/serverless-file-archiver) app, which stores the downloaded data in an S3 bucket.

## Deployment

Deploying this serverless app to your AWS account is quick and easy using [AWS CloudFormation](https://aws.amazon.com/cloudformation/). 

### Packaging

With the [AWS CLI](https://aws.amazon.com/cli/) installed, run the following command to upload the code to S3. You need to re-run this if you change the code in `archiver.py`. Be sure to set `DEPLOYMENT_S3_BUCKET` to a **bucket you own**; CloudFormation will copy the code function into a ZIP file in this S3 bucket, which can be deployed to AWS Lambda in the following steps. 

```sh
DEPLOYMENT_S3_BUCKET="YOUR_S3_BUCKET"
aws cloudformation package --template-file cloudformation.yaml --s3-bucket $DEPLOYMENT_S3_BUCKET \
  --output-template-file cloudformation-packaged.yaml
```

Now you will have `cloudformation-packaged.yaml`, which contains the full path to the ZIP file created by the previous step. 

### Configuring

Next, let's set the required configuration. You can set the following parameters:
 * `STACK_NAME` is the name of the CloudFormation stack that you'll create to manage all the resources (Lambda functions, CloudWatch Events, S3 buckets, IAM policies) associated with this app. You can set this to a new value to create a new instance with different parameters in your account, or use the same value when re-running to update parameters of an existing deployment.
 * `DOWNLOAD_URL` is the web address whose contents you want logged.
 * `SCHEDULE` is a [CloudWatch Event Schedule Expression](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html) at which to invoke this function.

```sh
STACK_NAME="serverless-feed-logger"
DOWNLOAD_URL="https://easweb.eas.ualberta.ca/weather_service.php?js"
SCHEDULE="rate(1 minute)"
```

With these configuration parameters defined, we can call `cloudformation deploy` to create the necessary resources in your AWS account:

```sh
aws cloudformation deploy --template-file cloudformation-packaged.yaml --capabilities CAPABILITY_IAM --parameter-overrides \
  "Schedule=$SCHEDULE" \
  "DownloadURL=$DOWNLOAD_URL" \
  --stack-name $STACK_NAME
````

If all went well, your stack has now been created. You can run the following to discover the name of the Log Group that will hold the Lambda's output, or go browse for it in the AWS Console.

```sh
aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs' --output text
```
