SELECT * FROM "AwsDataCatalog"."pyspark-database"."processed" limit 300;

SELECT 
    account_no, 
    SUM(COALESCE(withdrawal_sgd_amt, 0)) AS total_withdrawals_sgd, 
    SUM(COALESCE(deposit_sgd_amt, 0)) AS total_deposits_sgd
FROM "AwsDataCatalog"."pyspark-database"."processed" 
GROUP BY account_no;

------Total Deposit by Currency

SELECT
  deposit_currency,
  SUM(deposit_sgd_amt) AS total_deposit
FROM
  "AwsDataCatalog"."pyspark-database"."processed" 
GROUP BY
  deposit_currency;
  
  
SELECT 
    account_no, 
    SUM(COALESCE(deposit_sgd_amt, 0)) - SUM(COALESCE(withdrawal_sgd, 0)) AS balance_change_sgd
FROM "AwsDataCatalog"."pyspark-database"."processed"
GROUP BY account_no;


----Credit Worthiness 

SELECT 
    account_no,
    SUM(deposit_sgd_amt) AS total_deposits_sgd,
    SUM(withdrawal_sgd_amt) AS total_withdrawals_sgd,
    SUM(deposit_sgd_amt) / NULLIF(SUM(withdrawal_sgd_amt), 0) AS credit_ratio,
    CASE 
        WHEN SUM(deposit_sgd_amt) / NULLIF(SUM(withdrawal_sgd_amt), 0) > 1.5 THEN 'High Creditworthiness'
        WHEN SUM(deposit_sgd_amt) / NULLIF(SUM(withdrawal_sgd_amt), 0) BETWEEN 1.0 AND 1.5 THEN 'Moderate Creditworthiness'
        ELSE 'Low Creditworthiness'
    END AS creditworthiness
FROM "AwsDataCatalog"."pyspark-database"."processed"
GROUP BY account_no;

