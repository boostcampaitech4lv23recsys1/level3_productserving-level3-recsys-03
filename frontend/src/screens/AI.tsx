import { Button, Dialog } from "@mui/material";
import { doc, getDoc } from "firebase/firestore";
import React, { useEffect, useState } from "react";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { isDialogOpenAtom, userUIDAtom } from "../atoms";
import { db } from "../fbase";
import SpecificSolve from "./SpecificSolve";

import LoadingIcons from "react-loading-icons";

function AI() {
  const userUID = useRecoilValue(userUIDAtom);
  const [recProblem, setRecProblem] = useState<Array<string>>([]);
  const [incorrectArray, setIncorrectArray] = useState<
    Array<{
      problemCode: string;
      selected: number;
      timetaken: number;
      reviewed: boolean;
      cause: string;
    }>
  >([]);
  const isDialogOpen = useRecoilValue(isDialogOpenAtom);
  const setIsDialogOpen = useSetRecoilState(isDialogOpenAtom);

  const [isLoading, setIsLoading] = useState<Boolean>(false);

  useEffect(() => {
    getProfile();
  }, []);

  useEffect(() => {
    if (incorrectArray.length > 5) {
      getAnswer();
    }
  }, [incorrectArray]);

  const getProfile = async () => {
    const profile = await getDoc(doc(db, "users", String(userUID)));
    if (profile.exists()) {
      const solved = profile.data().solved;
      const incorrect = solved
        .slice(-100)
        .filter((x: { isCorrect: boolean }) => !x.isCorrect);
      setIncorrectArray(incorrect);
    }
  };

  const getAnswer = async () => {
    const randNumSet = new Set();
    // 수정 필요
    const incorrectArrayLength = incorrectArray.length;
    console.log(incorrectArrayLength);
    while (randNumSet.size < 5) {
      randNumSet.add(Math.floor(Math.random() * incorrectArrayLength));
    }
    const randNumArr: Array<any> = Array.from(randNumSet);
    console.log(randNumArr);
    const newRecProblem = [];
    while (randNumArr.length > 0) {
      const newAnswer = await getDoc(
        doc(db, "problems", incorrectArray[randNumArr.pop()]?.problemCode)
      );
      const newProblem = newAnswer.data()?.similar;
      newRecProblem.push(newProblem[Math.floor(Math.random() * 5)]);
    }
    setRecProblem(newRecProblem);
    setIsLoading(true);
  };

  return (
    <>
      <div style={{ margin: "0 0 5px 0", textAlign: "center" }}>
        <p>최근에 틀린 문제를 바탕으로 틀릴만한 문제를 AI가 추천해 줍니다.</p>
        <p>
          문제가 뜨지 않거나 똑같은 문제가 계속 뜬다면 '문제 풀기'로 가서 문제를
          더 풀어주세요.
        </p>
        <p>오답이 5문제 이상일 때 정상적으로 추천이 됩니다.</p>
        {isLoading ? (
          <Button
            style={{ backgroundColor: "#D5BCA2", color: "#37190F" }}
            variant="contained"
            onClick={() => {
              setIsDialogOpen(true);
            }}
          >
            AI 추천 문제
          </Button>
        ) : (
          <LoadingIcons.Grid fill="#D5BCA2" />
        )}
      </div>
      <Dialog
        fullWidth
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
      >
        <SpecificSolve pArray={recProblem} />
      </Dialog>
    </>
  );
}

export default AI;
