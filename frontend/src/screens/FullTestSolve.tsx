import React, { useEffect, useRef, useState } from "react";
import { ReactSketchCanvas, ReactSketchCanvasRef } from "react-sketch-canvas";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import Button from "@mui/material/Button";
import { useRecoilValue, useSetRecoilState } from "recoil";
import {
  isFullTestAtom,
  isSolvingAtom,
  roundOfExamAtom,
  userUIDAtom,
  diffOfExamAtom,
} from "../atoms";
import {
  arrayRemove,
  arrayUnion,
  doc,
  getDoc,
  setDoc,
  updateDoc,
} from "firebase/firestore";
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
import StarBorderIcon from "@mui/icons-material/StarBorder";

const styles = {
  border: "0.0625rem solid #9c9c9c",
  borderRadius: "0.25rem",
};

function FullTestSolve() {
  const windowHeight = window.innerHeight;
  const windowWidth = window.innerWidth;
  const canvasRef = useRef<ReactSketchCanvasRef>(null);
  const userUID = useRecoilValue(userUIDAtom);
  const isFullTest = useRecoilValue(isFullTestAtom);
  const diffOfExam = useRecoilValue(diffOfExamAtom);
  const roundOfExam = useRecoilValue(roundOfExamAtom);
  const setIsSolving = useSetRecoilState(isSolvingAtom);
  const [pointer, setPointer] = useState("all");
  const [qNum, setQNum] = useState(1);
  const [answerArray, setAnswerArray] = useState([]);
  const [timeArray, setTimeArray] = useState([[qNum, new Date().getTime()]]);
  const [timeTaken, setTimeTaken] = useState<Array<number>>([]);
  const [currentTime, setCurrentTime] = useState(new Date().getTime());
  const [restTime, setRestTime] = useState("");
  const [isEraseMode, setIsEraseMode] = useState(false);
  const [testInfo, setTestInfo] = useState<
    Array<{ answer: Number; score: Number; commentLink: URL }>
  >([]);
  const [isFinish, setIsFinish] = useState(false);
  const numArray = diffOfExam === "basic" ? [1, 2, 3, 4] : [1, 2, 3, 4, 5];

  const [jjimArray, setJjimArray] = useState<Array<string>>([]);

  useEffect(() => {
    const id = setInterval(() => {
      const newCurrentTime = new Date().getTime();
      setCurrentTime(newCurrentTime);
      const fullTime = diffOfExam === "basic" ? 70 * 60 * 1000 : 80 * 60 * 1000;
      let newRestTime = Math.trunc(
        (fullTime - (newCurrentTime - timeArray[0][1])) / 1000
      );
      const secs = newRestTime % 60;
      newRestTime = (newRestTime - secs) / 60;
      const mins = newRestTime;
      setRestTime(`${mins}:${secs}`);
      if (mins === 0 && secs === 0) {
        setIsFinish(true);
      }
    }, 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    getTestInfo();
  }, []);

  useEffect(() => {
    handleSolvingChange();
  }, [isFinish]);

  useEffect(() => {
    getJjimList();
  }, [jjimArray]);

  const getJjimList = async () => {
    const profile = await getDoc(doc(db, "users", String(userUID)));
    if (profile.exists()) {
      setJjimArray(profile.data().jjimlist);
    }
  };

  const handleClickNextButton = () => {
    const newTimeArray: any = [...timeArray];
    const currentNumber: number = qNum;
    canvasRef.current?.clearCanvas();
    setQNum(currentNumber + 1);
    newTimeArray.push([currentNumber + 1, new Date().getTime()]);
    setTimeArray(newTimeArray);
  };

  const handleClickPrevButton = () => {
    const newTimeArray: any = [...timeArray];
    const currentNumber = qNum;
    canvasRef.current?.clearCanvas();
    setQNum(currentNumber - 1);
    newTimeArray.push([currentNumber - 1, new Date().getTime()]);
    setTimeArray(newTimeArray);
  };

  const handleSolvingChange = async () => {
    const finalAnswerArray = [...answerArray];
    const finalTimeArray = [...timeArray, [-1, new Date().getTime()]];

    const times: number[] = [];
    for (let i = 0; i < finalTimeArray.length - 1; i++) {
      if (times[finalTimeArray[i][0]]) {
        times[finalTimeArray[i][0]] +=
          finalTimeArray[i + 1][1] - finalTimeArray[i][1];
      } else {
        times[finalTimeArray[i][0]] =
          finalTimeArray[i + 1][1] - finalTimeArray[i][1];
      }
    }
    setTimeTaken(times);
    for (let i = 1; i < times.length; i++) {
      if (finalAnswerArray[i] > 0) {
        let qCode = diffOfExam + roundOfExam + i.toString().padStart(2, "0");
        await setDoc(
          doc(db, "problems", qCode),
          {
            users: arrayUnion({
              userUID: userUID ? userUID : undefined,
              selected: finalAnswerArray[i] ? finalAnswerArray[i] : 0,
              timetaken: times[i] ? times[i] : undefined,
              solvedAt: currentTime ? currentTime : undefined,
              testMode: isFullTest,
              isCorrect: finalAnswerArray[i] === testInfo[i - 1].answer,
            }),
          },
          { merge: true }
        );
        await setDoc(
          doc(db, "users", String(userUID)),
          {
            solved: arrayUnion({
              problemCode: qCode,
              selected: finalAnswerArray[i] ? finalAnswerArray[i] : 0,
              timetaken: times[i] ? times[i] : undefined,
              solvedAt: currentTime ? currentTime : undefined,
              testMode: isFullTest,
              isCorrect: finalAnswerArray[i] === testInfo[i - 1].answer,
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
              selected: finalAnswerArray[i] ? finalAnswerArray[i] : 0,
              timetaken: times[i] ? times[i] : undefined,
              solvedAt: currentTime ? currentTime : undefined,
              testMode: isFullTest,
              isCorrect: finalAnswerArray[i] === testInfo[i - 1].answer,
            }),
          },
          { merge: true }
        );
        if (finalAnswerArray[i] !== testInfo[i - 1].answer) {
          await setDoc(
            doc(db, "users", String(userUID)),
            {
              incorrect: arrayUnion({
                problemCode: qCode,
                selected: finalAnswerArray[i] ? finalAnswerArray[i] : 0,
                timetaken: times[i] ? times[i] : undefined,
                reviewed: false,
                cause: "",
              }),
            },
            { merge: true }
          );
        }
      }
    }
  };

  let examCode: String = diffOfExam + " " + roundOfExam + "회";

  const getTestInfo = async () => {
    const qArray = [];
    for (let i = 1; i < 51; i++) {
      let qCode = diffOfExam + roundOfExam + i.toString().padStart(2, "0");
      const docSnap = await getDoc(doc(db, "problems", qCode));
      if (docSnap.exists()) {
        qArray.push({
          answer: docSnap.data().answer,
          score: docSnap.data().score,
          commentLink: docSnap.data().commentLink,
        });
      }
    }
    setTestInfo(qArray);
  };

  const totalScore = () => {
    let totalScore = 0;
    testInfo.map((q, i) => {
      if (answerArray[i + 1] === q.answer) {
        totalScore += Number(q.score);
      }
    });
    return totalScore;
  };

  const deleteJjimList = async (p: string) => {
    await updateDoc(doc(db, "users", String(userUID)), {
      jjimlist: arrayRemove(p),
    });
    setJjimArray([...jjimArray].filter((x) => x !== p));
  };

  const addJjimList = async (p: string) => {
    await setDoc(
      doc(db, "users", String(userUID)),
      {
        jjimlist: arrayUnion(p),
      },
      { merge: true }
    );
    setJjimArray([...jjimArray, p]);
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
      <div style={{ width: "95%", height: "5%" }}>남은 시간 : {restTime}</div>
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
          backgroundImage={`https://storage.googleapis.com/gildong-k-history/${
            diffOfExam + "/" + roundOfExam + "/" + (qNum - 1).toString()
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
        <Button
          size="small"
          variant="contained"
          style={{ marginLeft: "5px", marginRight: "10px", fontSize: "0.5rem" }}
          onClick={() => {
            canvasRef.current?.clearCanvas();
          }}
        >
          모두 지우기
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
          label="필기 모드"
        />
      </div>
      <div style={{ textAlign: "center" }}>
        <FormControl>
          <RadioGroup
            row
            aria-labelledby="demo-row-radio-buttons-group-label"
            name="row-radio-buttons-group"
            onChange={(event) => {
              const newAnswerArray: any = [...answerArray];
              newAnswerArray[qNum] = Number(event.target.value);
              setAnswerArray(newAnswerArray);
            }}
            value={answerArray[qNum] ? answerArray[qNum] : 0}
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
          disabled={qNum === 1}
          onClick={() => handleClickPrevButton()}
          style={{ width: "30%", fontSize: "10%", marginLeft: "5px" }}
        >
          이전 문제
        </Button>
        <Button
          variant="contained"
          disabled={qNum === 50}
          onClick={() => {
            handleClickNextButton();
          }}
          style={{ width: "30%", fontSize: "10%", marginLeft: "5px" }}
        >
          다음 문제
        </Button>
        <Button
          variant="contained"
          onClick={() => setIsFinish(true)}
          style={{ width: "30%", fontSize: "10%", marginLeft: "5px" }}
        >
          제출하고 나가기
        </Button>
      </div>
      <div>
        <Dialog
          open={isFinish}
          onClose={() => {
            setIsSolving(false);
          }}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle>
            {`${
              examCode.slice(0, -4) === "basic" ? "기본" : "심화"
            } ${examCode.slice(-4)} 테스트 결과 : ${totalScore()}점`}
          </DialogTitle>
          <DialogContent>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>문항 번호</TableCell>
                    <TableCell>제출 답안</TableCell>
                    <TableCell>정답</TableCell>
                    <TableCell>해설</TableCell>
                    <TableCell>배점</TableCell>
                    <TableCell>찜하기</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {testInfo.map((q, i) => (
                    <TableRow
                      style={
                        answerArray[i + 1] !== q.answer
                          ? { backgroundColor: "#fd7171" }
                          : {}
                      }
                    >
                      <TableCell>{`${i + 1}번`}</TableCell>
                      <TableCell>{answerArray[i + 1]}</TableCell>
                      <TableCell
                        onClick={() => {
                          window.open(q.commentLink, "_blank");
                        }}
                      >
                        link
                      </TableCell>
                      <TableCell>{String(q.answer)}</TableCell>
                      <TableCell>{String(q.score)}</TableCell>
                      <TableCell>
                        <Button
                          onClick={() => {
                            const p =
                              diffOfExam +
                              roundOfExam +
                              (i + 1).toString().padStart(2, "0");
                            jjimArray?.indexOf(p) === -1
                              ? addJjimList(p)
                              : deleteJjimList(p);
                          }}
                        >
                          {jjimArray?.indexOf(
                            diffOfExam +
                              roundOfExam +
                              (i + 1).toString().padStart(2, "0")
                          ) === -1 ? (
                            <StarBorderIcon />
                          ) : (
                            <StarIcon />
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
export default FullTestSolve;
