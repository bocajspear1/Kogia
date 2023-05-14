const users = require('@arangodb/users');

pass = require('internal').genRandomAlphaNumbers(20);

users.save('kogia', pass);
db._createDatabase("kogia");
users.grantDatabase("kogia", "kogia", 'rw');

console.log(pass)