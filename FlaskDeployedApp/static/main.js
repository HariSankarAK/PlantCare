// setting up firebase with our website
const firebaseConfig = {
  apiKey: "AIzaSyC4OVwLXeh54-feikcHU9c509fjuYvbviI",
  authDomain: "plantcare-f3921.firebaseapp.com",
  projectId: "plantcare-f3921",
  storageBucket: "plantcare-f3921.appspot.com",
  messagingSenderId: "204577373555",
  appId: "1:204577373555:web:3f3d5c51ad11aab55e1906"
};
firebase.initializeApp(firebaseConfig);


const db = firebase.firestore();
const auth = firebase.auth();

// function to send the user's auth token to the backend
const sendTokenToBackend = (token) => {
  fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({token: token})
  })
  .then(response => {
    if (response.ok) {
      console.log('Token sent to backend');
    } else {
      console.log('Failed to send token to backend');
    }
  })
  .catch(error => {
    console.log('Error sending token to backend:', error);
  });
}


// Sign up function
const signUp = () => {
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const location = document.getElementById("location").value;
  console.log(email, password);
  // firebase code
  firebase.auth().createUserWithEmailAndPassword(email, password)
  .then((result) => {
    const uid = result.user.uid;
    const userRef = db.collection("users").doc(uid);
    userRef.set({
      uid: uid,
      username: username,
      email: email,
      location: location
    })
    .then(() => {
      console.log("Data was successfully written to Firestore!");
      document.write("You are Signed Up");
      window.location.href = "signIn.html";
    })
    .catch((error) => {
      console.log("Failed to write data to Firestore:", error.message);
    });
  })
  .catch((error) => {
    console.log(error.code);
    console.log(error.message);
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
      result.user.getIdToken().then((idToken) => {
        // send the user's auth token to the backend
        sendTokenToBackend(idToken);
      });
      document.write("You are Signed In");
      window.location.href = "http://127.0.0.1:5000/home";
      console.log(result);
    })
    .catch((error) => {
      console.log(error.code);
      console.log(error.message);
      const errorMessage = document.getElementById("error-message");
      errorMessage.innerText = "You are not registered.";
    });
}
const offsignIn = () => {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const officeCode = document.getElementById("office-code").value; // get the office code value from the input field
  
  // firebase code
  firebase.auth().signInWithEmailAndPassword(email, password)
    .then((result) => {
      // Signed in 
      result.user.getIdToken().then((idToken) => {
        // send the user's auth token to the backend
        sendTokenToBackend(idToken);
      });

      // Verify office code
      const validOfficeCodes = ['office1', 'office2', 'office3']; // set of valid office codes
      if (validOfficeCodes.includes(officeCode)) {
        // Redirect to next page
        window.location.href = "http://127.0.0.1:5000/offhome";
      } else {
        // Show error message
        const errorMessage = document.getElementById("error-message");
        errorMessage.innerText = "Invalid office code.";
      }
      
      console.log(result);
    })
    .catch((error) => {
      console.log(error.code);
      console.log(error.message);
      const errorMessage = document.getElementById("error-message");
      errorMessage.innerText = "You are not registered.";
    });
}
