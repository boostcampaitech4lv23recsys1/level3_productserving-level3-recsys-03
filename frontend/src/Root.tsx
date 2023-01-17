import React, { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { isLoggedInAtom, isSolvingAtom, userUIDAtom } from "./atoms";
import Auth from "./Auth";
import Footer from "./components/Footer";
import { getAuth } from "./fbase";

function Root() {
  const isLoggedIn = useRecoilValue(isLoggedInAtom);
  const setIsLoggedIn = useSetRecoilState(isLoggedInAtom);
  const setUserUID = useSetRecoilState(userUIDAtom);
  const isSolving = useRecoilValue(isSolvingAtom);
  useEffect(() => {
    getAuth().onAuthStateChanged((user) => {
      if (user) {
        setIsLoggedIn(true);
        setUserUID(user.uid);
      } else {
        setIsLoggedIn(false);
      }
    });
  }, []);
  return (
    <div className="Root">
      {isLoggedIn ? <Outlet /> : <Auth />}
      {isSolving ? <></> : <Footer />}
    </div>
  );
}

export default Root;
