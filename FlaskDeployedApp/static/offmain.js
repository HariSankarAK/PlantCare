// setting up firebase with our website
const firebaseApp = firebase.initializeApp({
    apiKey: "AIzaSyBgc34BZLWBl54MBC8ElfRNphKeH_XQP14",
  authDomain: "plantcare-c1241.firebaseapp.com",
  projectId: "plantcare-c1241",
  storageBucket: "plantcare-c1241.appspot.com",
  messagingSenderId: "48035744902",
  appId: "1:48035744902:web:9c86f426022a80fedbd507",
  measurementId: "G-YWDRRCMREC"
});
const db = firebaseApp.firestore();
const auth = firebaseApp.auth();

// Sign up function
const signUp = () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    console.log(email, password)
    // firebase code
    firebase.auth().createUserWithEmailAndPassword(email, password)
        .then((result) => {
            // Signed in 
            document.write("You are Signed Up")
            console.log(result)
            window.location.href = "signIn.html";
            // ...
        })
        .catch((error) => {
            console.log(error.code);
            console.log(error.message)
            // ..
        });
}

// Sign In function
const signIn = () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    // firebase code
    firebase.auth().signInWithEmailAndPassword(email, password)
        .then((result) => {
            // Signed in 
            document.write("You are Signed In")
            window.location.href = "http://127.0.0.1:5000/offhome";
            console.log(result)
        })
        .catch((error) => {
            console.log(error.code);
            console.log(error.message);
            const errorMessage = document.getElementById("error-message");
            errorMessage.innerText = "You are not registered.";
        });
}
