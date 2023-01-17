import React from "react";
import FullTestSolve from "./FullTestSolve";
import Fulltest from "./Fulltest";
import { Button } from "@mui/material";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { diffOfExamAtom, isSolvingAtom, roundOfExamAtom } from "../atoms";
import RandomSolve from "./RandomSolve";

function QRef() {
  const isSolving = useRecoilValue(isSolvingAtom);
  const roundOfExam = useRecoilValue(roundOfExamAtom);
  const setIsSolving = useSetRecoilState(isSolvingAtom);
  const setRoundOfExam = useSetRecoilState(roundOfExamAtom);
  const setDiffOfExam = useSetRecoilState(diffOfExamAtom);
  const handleSolvingChange = (event: React.MouseEvent<HTMLElement>) => {
    setIsSolving(true);
  };

  return (
    <div style={{ textAlign: "center" }}>
      {isSolving ? (
        roundOfExam === "랜덤" ? (
          <RandomSolve />
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
          </div>
        </>
      )}
    </div>
  );
}

export default QRef;
