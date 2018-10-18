const admin = require('firebase-admin');
const keys = require('./key.json');
const spawn = require('child_process').spawn;
const fs = require('fs');

const py = spawn("python", ["-u", "cnn_script.py"]);
py.stdout.setEncoding('utf-8');
py.on('exit', () => {
    console.log('PYTHON SCRIPT ERROR');
});

admin.initializeApp({
    credential: admin.credential.cert(keys),
    databaseURL: "https://melonoma-a896a.firebaseio.com",
    storageBucket: "gs://melonoma-a896a.appspot.com"
});
const db = admin.firestore();

let jobs = {};

function processUpload(id) {
    jobs[id] = true;
    py.stdin.write(JSON.stringify({id}) + '\n'); //send off to script to process
}

py.stdout.on('data', (data) => {
    let result = JSON.parse(data); // json result
    result.processed = true;
    console.log(result);
    fs.unlink(`tmp/${result.id}`, (error) => { /* handle error */ }); // delete file
    db.doc(`uploads/${result.id}`).update(result).then(() => { // update change
        delete jobs[result.id];
    });
});

db.collection('uploads').where('processed', '==', false).onSnapshot(docs => {
    docs.forEach(doc => {
        if (jobs[doc.id] !== undefined) return;
        admin.storage().bucket().file(doc.id).createReadStream().pipe(fs.createWriteStream(`tmp/${doc.id}`).on('finish', () => {
            processUpload(doc.id);
        }));
    });
});

process.stdin.resume();
