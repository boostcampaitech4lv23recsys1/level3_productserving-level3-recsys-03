import React, { useEffect, useRef, useState } from "react";
import { ReactSketchCanvas, ReactSketchCanvasRef } from "react-sketch-canvas";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import Button from "@mui/material/Button";
import { useRecoilValue, useSetRecoilState } from "recoil";
import {
  diffOfExamAtom,
  isFullTestAtom,
  isSolvingAtom,
  userUIDAtom,
} from "../atoms";
import { arrayUnion, doc, getDoc, setDoc } from "firebase/firestore";
import { db } from "../fbase";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Paper,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import StarIcon from "@mui/icons-material/Star";
import SpecificSolve from "./SpecificSolve";

const styles = {
  border: "0.0625rem solid #9c9c9c",
  borderRadius: "0.25rem",
};
function RandomSolve() {
  const windowHeight = window.innerHeight;
  const windowWidth = window.innerWidth;
  const canvasRef = useRef<ReactSketchCanvasRef>(null);
  const userUID = useRecoilValue(userUIDAtom);
  const isFullTest = useRecoilValue(isFullTestAtom);
  const setIsSolving = useSetRecoilState(isSolvingAtom);
  const diffOfExam = useRecoilValue(diffOfExamAtom);
  const [pointer, setPointer] = useState("all");
  const [startTime, setStartTime] = useState(new Date().getTime());
  const [isEraseMode, setIsEraseMode] = useState(false);
  const [selected, setSelected] = useState(0);
  const [pArray, setPArray] = useState<Array<string>>([]);
  const [randNumArray, setRandNumArray] = useState<Array<number>>([]);
  const [currentNum, setCurrentNum] = useState(0);
  const [answer, setAnswer] = useState(0);
  const [score, setScore] = useState(0);
  const [solved, setSolved] = useState(false);
  const [roundOfExam, setRoundOfExam] = useState<string>("");
  const [qNum, setQNum] = useState<number>(0);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    const { randomRound, randomQNum } = getNewProblem();
    setRoundOfExam(randomRound);
    setQNum(randomQNum);
  }, []);

  useEffect(() => {
    getAnswer();
  }, [qNum]);

  const getAnswer = async () => {
    const qCode = diffOfExam + roundOfExam + qNum?.toString().padStart(2, "0");
    const newAnswer = await getDoc(doc(db, "problems", qCode));
    setAnswer(newAnswer.data()?.answer);
    setScore(newAnswer.data()?.score);
    setPArray(newAnswer.data()?.similar)
  };

  const numArray = diffOfExam === "basic" ? [1, 2, 3, 4] : [1, 2, 3, 4, 5];

  const getNewProblem = () => {
    const roundArray =
      diffOfExam === "basic"
        ? [
            "47",
            "48",
            "49",
            "50",
            "51",
            "52",
            "54",
            "55",
            "57",
            "58",
            "60",
            "61",
          ]
        : [
            "47",
            "48",
            "49",
            "50",
            "51",
            "52",
            "53",
            "54",
            "55",
            "56",
            "57",
            "58",
            "59",
            "60",
            "61",
            "62",
          ];
    const randomRound =
      roundArray[Math.floor(Math.random() * roundArray.length)];
    const randomQNum = Math.ceil(Math.random() * 50);
    return { randomRound, randomQNum };
  };

  const handleClickNextButton = async () => {
    const qCode = diffOfExam + roundOfExam + qNum?.toString().padStart(2, "0");
    const endTime = new Date().getTime();
    canvasRef.current?.exportPaths().then(async (result: any) => {
      await setDoc(
        doc(db, "problems", qCode),
        {
          users: arrayUnion({
            userUID: userUID ? userUID : undefined,
            selected: selected,
            timetaken: endTime - startTime,
            solvedAt: endTime,
            testMode: false,
            isCorrect: answer === selected,
          }),
        },
        { merge: true }
      );
      await setDoc(
        doc(db, "users", String(userUID)),
        {
          solved: arrayUnion({
            problemCode: qCode,
            selected: selected,
            timetaken: endTime - startTime,
            solvedAt: endTime,
            testMode: false,
            isCorrect: answer === selected,
          }),
        },
        { merge: true }
      );
      await setDoc(
        doc(db, "logs", "solved"),
        {
          solved: arrayUnion({
            userUID: userUID ? userUID : undefined,
            problemCode: qCode,
            selected: selected,
            timetaken: endTime - startTime,
            solvedAt: endTime,
            testMode: false,
            isCorrect: answer === selected,
          }),
        },
        { merge: true }
      );
      if (answer !== selected) {
        await setDoc(
          doc(db, "users", String(userUID)),
          {
            incorrect: arrayUnion({
              problemCode: qCode,
              selected: selected,
              timetaken: endTime - startTime,
              reviewed: false,
              cause: "",
            }),
          },
          { merge: true }
        );
      }
    });
    canvasRef.current?.clearCanvas();
    setSolved(true);
  };
  return (
    <div
      style={{
        height: `${windowHeight}px`,
        width: `${windowWidth * 0.95}px`,
        backgroundColor: "#FCF6F5",
        overflow: "scroll",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          width: "95%",
          height: "75%",
          // backgroundImage: `url(https://storage.cloud.google.com/gildong-k-history/${
          //   diffOfExam + '/' + roundOfExam +'/' + (qNum-1).toString()
          // }.png)`,
          // backgroundRepeat: 'no-repeat',
          // backgroundSize: 'contain',
          // backgroundPosition:'center',
        }}
      >
        <ReactSketchCanvas
          style={styles}
          ref={canvasRef}
          width="100%"
          height="100%"
          strokeWidth={1}
          eraserWidth={30}
          strokeColor="black"
          canvasColor="transparent"
          allowOnlyPointerType={pointer}
          backgroundImage={dialogOpen?'':`https://storage.googleapis.com/gildong-k-history/${
            diffOfExam + "/" + roundOfExam + "/" + qNum.toString()
          }.png`}
          preserveBackgroundImageAspectRatio="xMidYMid meet"
        />
      </div>
      <div style={{ paddingBottom: "5px" }}>
        <Button
          size="small"
          variant="contained"
          style={{ marginLeft: "5px", marginRight: "10px", fontSize: "0.5rem" }}
          onClick={() => {
            const newEraseMode = !isEraseMode;
            setIsEraseMode(newEraseMode);
            canvasRef.current?.eraseMode(newEraseMode);
          }}
        >
          {isEraseMode ? "펜" : "지우개"}
        </Button>
        <FormControlLabel
          control={
            <Switch
              checked={pointer === "all"}
              onChange={() => {
                pointer === "all" ? setPointer("pen") : setPointer("all");
              }}
              inputProps={{ "aria-label": "controlled" }}
            />
          }
          label="손가락으로 쓰기"
        />
      </div>
      <div style={{ textAlign: "center" }}>
        <FormControl>
          <RadioGroup
            row
            aria-labelledby="demo-row-radio-buttons-group-label"
            name="row-radio-buttons-group"
            onChange={(event) => {
              setSelected(Number(event.target.value));
            }}
            value={selected}
          >
            {numArray.map((num) => (
              <FormControlLabel
                value={num}
                control={<Radio size="small" />}
                label={num}
              />
            ))}
          </RadioGroup>
        </FormControl>
      </div>
      <div>
        <Button
          variant="contained"
          onClick={() => {
            handleClickNextButton();
          }}
          style={{ width: "30%", fontSize: "10%", marginLeft: "5px" }}
        >
          다음 문제
        </Button>
        <Button
          variant="contained"
          onClick={() => setIsSolving(false)}
          style={{ width: "30%", fontSize: "10%", marginLeft: "5px" }}
        >
          나가기
        </Button>
      </div>
      <div>
        <Dialog
          open={solved}
          onClose={() => {
            setSolved(false);
            const { randomRound, randomQNum } = getNewProblem();
            setRoundOfExam(randomRound);
            setQNum(randomQNum);
            setSelected(0);
          }}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle>
            {`테스트 결과 : ${
              answer === selected ? "정답입니다" : "틀렸습니다"
            }`}
          </DialogTitle>
          <DialogContent>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>문항 번호</TableCell>
                    <TableCell>제출 답안</TableCell>
                    <TableCell>정답</TableCell>
                    <TableCell>찜하기</TableCell>
                    <TableCell>유사 문제 풀기</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow
                    style={
                      selected !== answer ? { backgroundColor: "#fd7171" } : {}
                    }
                  >
                    <TableCell>
                      {diffOfExam +
                        roundOfExam +
                        qNum?.toString().padStart(2, "0")}
                    </TableCell>
                    <TableCell>{selected}</TableCell>
                    <TableCell>{answer}</TableCell>
                    <TableCell>
                      <Button
                        onClick={async () => {
                          await setDoc(
                            doc(db, "users", String(userUID)),
                            {
                              jjimlist: arrayUnion(
                                diffOfExam +
                                  roundOfExam +
                                  qNum?.toString().padStart(2, "0")
                              ),
                            },
                            { merge: true }
                          );
                        }}
                      >
                        <StarIcon />
                      </Button>
                    </TableCell>
                    <TableCell>
                      <Button
                        onClick={()=>{setDialogOpen(true)
                        console.log(pArray)}}>
                        5문항 풀기
                      </Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </DialogContent>
        </Dialog>
        <Dialog fullWidth open={dialogOpen} onClose={() => setDialogOpen(false)}>
          <SpecificSolve pArray={pArray} />
        </Dialog>
      </div>
    </div>
  );
}
export default RandomSolve;
