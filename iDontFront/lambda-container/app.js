// exports.handler = async (event) => {
//     const response = {
//         statusCode: 200,
//         body: JSON.stringify('Hello from Lambda!'),
//     };
//     return response;
// };

// exports.handler = function (event, context) {
// 	console.log("event");
// 	console.log(event);
// 	// context.succeed('hello ' + event.name);
// 	return "YES!!!"
// };
exports.handler = async (event) => {
    const min = 1;
    const max = 6;    
    const randomNumber = Math.floor(
      Math.random() * (max - min + 1)
    ) + min;
    const message = 'Your dice throw resulted in: ' +
      randomNumber;
    return message;
  };