import { setDoc, doc } from "@firebase/firestore";
import {
  signInWithPopup,
  getAuth,
  GoogleAuthProvider,
  provider,
  db,
} from "./fbase";
import React from "react";

const Auth = () => {
  const auth = getAuth();
  console.log(auth.currentUser);
  const signInWithGoogle = async () => {
    signInWithPopup(auth, provider)
      .then(async (result) => {
        const user = result.user;
        console.log(user);
        if(user.metadata.creationTime === user.metadata.lastSignInTime){
          try{
            await setDoc(doc(db, "users", user.uid), {
              uid: user.uid,
              solved: [],
              incorrect: []
            })
          } catch(e){
            console.error(e)
          }
        }
      })
      .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        const email = error.email;
        const credential = GoogleAuthProvider.credentialFromError(error);
        console.log(errorCode, errorMessage, email, credential);
      });
  };
  
  const onClick = () => {
    signInWithGoogle();
    console.log("click");
  };
  return (
    <div>
      <div>
        <button onClick={onClick}>Continue with Google Login</button>
      </div>
    </div>
  );
};
export default Auth;
