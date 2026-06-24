# AWS Serverless VPC Flow Logs Analytics Pipeline

A production-ready, serverless data pipeline designed to ingest, transform, and analyze AWS VPC Flow Logs in real-time. This project demonstrates how to capture network traffic, process it using AWS Lambda, and run SQL queries via Amazon Athena for security analysis and compliance auditing.

## Architecture Overview
The pipeline routes network logs from CloudWatch through the following components:
* **VPC Flow Logs** -> Captured and streamed via CloudWatch Log Groups.
* **Amazon Kinesis Data Firehose** -> Buffers and delivers data streams.
* **AWS Lambda (Python)** -> Decodes Base64, decompresses Gzip payloads, extracts raw log events, and cleanses data.
* **Amazon S3** -> Stores the structured logs partitioned by date.
* **Amazon Athena** -> Queries network traffic using standard SQL.

## Technical Challenges & Troubleshooting (Lessons Learned)

### 1. Data Transformation & Nested Payloads
* **Problem:** Raw VPC Flow Logs wrapped in CloudWatch log events arrive at Kinesis Firehose compressed in `Gzip` format and encoded in `Base64`. Standard Athena tables could not parse the nested text, resulting in skewed and unreadable columns.
* **Solution:** Developed a custom Python Lambda function to programmatically handle the extraction. The script decodes the Base64 layer, checks and decompresses the Gzip payload, parses the CloudWatch JSON wrapper, and outputs clean, newline-delimited log records into S3.

### 2. Lambda Task Timeouts (Concurrency & Batching)
* **Problem:** Initially, the Lambda function threw frequent `Task timed out after 3.00 seconds` errors, causing data delivery failures.
* **Root Cause:** Kinesis Firehose buffers data and sends it in heavy batches. The combination of Lambda "Cold Starts", parsing massive JSON blocks, and executing CPU-heavy `gzip.decompress()` operations exhausted the default 3-second timeout limit.
* **Solution:** Optimized the Lambda configuration by increasing the timeout threshold to 1 minute. This provided enough runway for processing high-throughput batches seamlessly without failing the pipeline.

## Athena Query Examples

### Top 5 Blocked IP Addresses (Security Analysis)
```sql
SELECT srcaddr, COUNT(*) as reject_count
FROM vpc_flow_logs
WHERE action = 'REJECT'
GROUP BY srcaddr
ORDER BY reject_count DESC
LIMIT 5;
