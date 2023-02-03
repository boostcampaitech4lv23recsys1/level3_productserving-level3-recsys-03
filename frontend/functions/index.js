const functions = require("firebase-functions");
const Client = require("node-rest-client").Client;
const client = new Client();
const cors = require("cors")({origin: true});

exports.getRecentSolved = functions.https.onRequest((req, res) => {
  cors(req, res, () => {
    functions.logger.info("Hello logs!", {structuredData: true});
    client.get(
        `http://27.96.130.82:30001/db${req.originalUrl}/advanced`,
        function(data, response) {
          console.log(data, response);
          res.send(data);
        }
    );
  });
});

exports.getRecProblems = functions.https.onRequest((req, res) => {
  cors(req, res, () => {
    functions.logger.info("Hello logs!", {structuredData: true});
    client.get(
        `http://27.96.130.82:30001/model/advanced${req.originalUrl}`,
        function(data, response) {
          console.log(data, response);
          res.send(data);
        }
    );
  });
});
