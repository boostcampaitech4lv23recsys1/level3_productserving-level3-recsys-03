import React, { useEffect, useState } from "react";
import FullTestSolve from "./FullTestSolve";
import Fulltest from "./Fulltest";
import { Button } from "@mui/material";
import { useRecoilValue, useSetRecoilState } from "recoil";
import {
  diffOfExamAtom,
  isSolvingAtom,
  roundOfExamAtom,
  userUIDAtom,
} from "../atoms";
import RandomSolve from "./RandomSolve";
import RecSolve from "./RecSolve";

function QRef() {
  const userUID = useRecoilValue(userUIDAtom);
  const isSolving = useRecoilValue(isSolvingAtom);
  const roundOfExam = useRecoilValue(roundOfExamAtom);
  const setIsSolving = useSetRecoilState(isSolvingAtom);
  const setRoundOfExam = useSetRecoilState(roundOfExamAtom);
  const setDiffOfExam = useSetRecoilState(diffOfExamAtom);
  const handleSolvingChange = (event: React.MouseEvent<HTMLElement>) => {
    setIsSolving(true);
  };
  const [recProblem, setRecProblem] = useState<Array<string>>([]);
  const [solvedArray, setSolvedArray] = useState<Array<string>>([]);
  const [model, setModel] = useState<string>("");

  useEffect(() => {
    fetch(
      `https://us-central1-gildong-k-history.cloudfunctions.net/getRecentSolved/${userUID}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      }
    )
      .then((res) => res.json())
      .then((data) => {
        if(data.length>30){
          getRecProblem("advanced", data)
        }
      });
  }, []);

  const getRecProblem = (diff: string, solvedArr:Array<string>) => {
    fetch(
      `https://us-central1-gildong-k-history.cloudfunctions.net/getRecProblems/${userUID}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      }
    )
      .then((res) => res.json())
      .then(
        (data: {
          [key: string]: { recommend: Array<string>; random: Array<string> };
        }) => {
          setModel(Object.keys(data)[0]);
          const newRecProblem = [];
          for (let i = 0; i < 5; i++) {
            newRecProblem.push(data[Object.keys(data)[0]].recommend[i]);
            newRecProblem.push(data[Object.keys(data)[0]].random[i]);
          }
          setRecProblem(newRecProblem);
          setSolvedArray(solvedArr);
        }
      );
  };

  return (
    <div style={{ textAlign: "center" }}>
      {isSolving ? (
        roundOfExam === "랜덤" ? (
          <RandomSolve />
        ) : roundOfExam === "recommend" ? (
          <RecSolve pArray={recProblem} model={model} />
        ) : (
          <FullTestSolve />
        )
      ) : (
        <>
          <Fulltest />
          <div style={{ margin: "0 0 5px 0" }}>
            <Button
              style={{ backgroundColor: "#D5BCA2", color: "#37190F" }}
              variant="contained"
              onClick={(e) => handleSolvingChange(e)}
            >
              풀기
            </Button>
          </div>
          <div style={{ margin: "0 0 5px 0" }}>
            <Button
              style={{ backgroundColor: "#D5BCA2", color: "#37190F" }}
              variant="contained"
              onClick={(e) => {
                setDiffOfExam("basic");
                setRoundOfExam("랜덤");
                handleSolvingChange(e);
              }}
            >
              기본 랜덤 풀기
            </Button>
          </div>
          <div style={{ margin: "0 0 5px 0" }}>
            {solvedArray.length > 30 ? (
              <Button
                style={{
                  backgroundColor: "#D5BCA2",
                  color: "#37190F",
                }}
                variant="contained"
                onClick={(e) => {
                  setRoundOfExam("recommend");
                  handleSolvingChange(e);
                }}
              >
                심화 추천 문제
              </Button>
            ) : (
              <Button
                style={{ backgroundColor: "#D5BCA2", color: "#37190F" }}
                variant="contained"
                onClick={(e) => {
                  setDiffOfExam("advanced");
                  setRoundOfExam("랜덤");
                  handleSolvingChange(e);
                }}
              >
                심화 랜덤 풀기
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default QRef;
