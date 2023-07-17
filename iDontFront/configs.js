// const S3_BUCKET = "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com"
// const S3_COMPLETED_JSON = "/channels/completed-jsons/completed-captions/completed.json"

module.exports = {
    database: {
      host: process.env.DB_HOST || 'localhost',
    },
    app: {
      port: process.env.APP_PORT || 3333
    },
    S3_BUCKET: "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com",
    S3_COMPLETED_JSON : "/channels/completed-jsons/completed-captions/completed.json",
    S3_STATE_OVERVIEW_JSON : "/channels/completed-jsons/overview-state/state.json"
  };
  