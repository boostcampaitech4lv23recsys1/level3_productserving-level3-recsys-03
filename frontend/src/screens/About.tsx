import { Button, Dialog } from "@mui/material";
import { doc, getDoc, Index } from "firebase/firestore";
import React, { useEffect, useState } from "react";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { isDialogOpenAtom, userUIDAtom } from "../atoms";
import { db } from "../fbase";
import SpecificSolve from "./SpecificSolve";

import LoadingIcons from "react-loading-icons";
import RecSolve from "./RecSolve";

function About() {
  const userUID = useRecoilValue(userUIDAtom);
  const [recProblem, setRecProblem] = useState<Array<string>>([])
  const [solvedArray, setSolvedArray] = useState<Array<string>>([]);
  const isDialogOpen = useRecoilValue(isDialogOpenAtom);
  const setIsDialogOpen = useSetRecoilState(isDialogOpenAtom);

  const [isLoading, setIsLoading] = useState<Boolean>(true);
  const [model, setModel] = useState<string>('')

  useEffect(() => {
    fetch(`https://us-central1-gildong-k-history.cloudfunctions.net/getRecentSolved`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data)
        setSolvedArray(data)});
  }, []);

  const getRecProblem = (diff: string) => {
    setIsLoading(false)
    fetch(`https://us-central1-gildong-k-history.cloudfunctions.net/getRecProblems`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    })
      .then((res) => res.json())
      .then((data:{[key:string]:{recommend:Array<string>, random: Array<string>}}) => {
        setModel(Object.keys(data)[0])
        const newRecProblem = []
        for(let i = 0; i<5; i++){
          newRecProblem.push(data[Object.keys(data)[0]].recommend[i])
          newRecProblem.push(data[Object.keys(data)[0]].random[i])
        }
        setRecProblem(newRecProblem)
        setIsLoading(true)
        setIsDialogOpen(true)
      });
  };

  return (
    <>
      <div style={{ margin: "0 0 5px 0", textAlign: "center" }}>
        <div>
          <img
            className="gildong-ai-class"
            src="gildong-ai.png"
            alt="길동 ai"
            style={{ maxHeight: "50vh", maxWidth: "100%" }}
          />
        </div>
        <div>
          {isLoading ? (
            <div style={{ display: "inline-grid" }}>
              {solvedArray.length >
              29 ? (
                <Button
                  style={{
                    width: "120px",
                    height: "80px",
                    backgroundColor: "#D5BCA2",
                    color: "#37190F",
                    marginTop: "5px",
                  }}
                  variant="contained"
                  onClick={() => {
                    getRecProblem("advanced");
                  }}
                >
                  심화 추천 문제
                </Button>
              ) : (
                <div
                  style={{
                    width: "120px",
                    height: "80px",
                    backgroundColor: "gray",
                    color: "white",
                    marginTop: "5px",
                    textAlign: "center",
                    borderRadius: "5px",
                  }}
                >
                  추천을 위한 기본 문제 풀이가 부족합니다
                </div>
              )}
            </div>
          ) : (
            <LoadingIcons.Grid fill="#D5BCA2" />
          )}
        </div>
      </div>
      <Dialog
        fullWidth
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
      >
        <RecSolve pArray={recProblem} model={model} />
      </Dialog>
    </>
  );
}

export default About;
