import React, { useEffect, useRef, useState } from "react";
import { ReactSketchCanvas, ReactSketchCanvasRef } from "react-sketch-canvas";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import Button from "@mui/material/Button";
import { useRecoilValue, useSetRecoilState } from "recoil";
import {
  isDialogOpenAtom,
  isFullTestAtom,
  isSolvingAtom,
  userUIDAtom,
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
function SpecificSolve(props: { pArray: Array<string> }) {
  const pArray = props.pArray;
  const windowHeight = window.innerHeight;
  const windowWidth = window.innerWidth;
  const canvasRef = useRef<ReactSketchCanvasRef>(null);
  const userUID = useRecoilValue(userUIDAtom);
  const isFullTest = useRecoilValue(isFullTestAtom);
  const setIsDialogOpen = useSetRecoilState(isDialogOpenAtom);
  const [pointer, setPointer] = useState("all");
  const [startTime, setStartTime] = useState(new Date().getTime());
  const [isEraseMode, setIsEraseMode] = useState(false);
  const [selected, setSelected] = useState(0);
  const [currentNum, setCurrentNum] = useState(0);
  const [answer, setAnswer] = useState(0);
  const [solved, setSolved] = useState(false);

  const [jjimArray, setJjimArray] = useState<Array<string>>([]);
  const [link, setLink] = useState<URL>();

  useEffect(() => {
    getAnswer();
  }, [currentNum, pArray]);
  const getAnswer = async () => {
    const newAnswer = await getDoc(
      doc(db, "problems", String(pArray[currentNum]))
    );
    setAnswer(newAnswer.data()?.answer);
    setLink(newAnswer.data()?.commentLink);
  };
  const diffOfExam = pArray[currentNum]?.slice(0, -4);
  const numArray = diffOfExam === "basic" ? [1, 2, 3, 4] : [1, 2, 3, 4, 5];

  useEffect(() => {
    getJjimList();
  }, [jjimArray]);

  const handleClickNextButton = async () => {
    const endTime = new Date().getTime();
    canvasRef.current?.exportPaths().then(async (result: any) => {
      await updateDoc(doc(db, "problems", String(pArray[currentNum])), {
        users: arrayUnion({
          userUID: userUID ? userUID : undefined,
          selected: selected,
          timetaken: endTime - startTime,
          solvedAt: endTime,
          testMode: isFullTest,
          isCorrect: answer === selected,
        }),
      });
      await updateDoc(doc(db, "users", String(userUID)), {
        solved: arrayUnion({
          problemCode: pArray[currentNum],
          selected: selected,
          timetaken: endTime - startTime,
          solvedAt: endTime,
          testMode: isFullTest,
          isCorrect: answer === selected,
        }),
      });
      await updateDoc(doc(db, "logs", "solved"), {
        solved: arrayUnion({
          userUID: userUID ? userUID : undefined,
          problemCode: pArray[currentNum],
          selected: selected,
          timetaken: endTime - startTime,
          solvedAt: endTime,
          testMode: isFullTest,
          isCorrect: answer === selected,
        }),
      });
      if (answer !== selected) {
        await updateDoc(doc(db, "users", String(userUID)), {
          incorrect: arrayUnion({
            problemCode: pArray[currentNum],
            selected: selected,
            timetaken: endTime - startTime,
            reviewed: false,
            cause: "",
          }),
        });
      }
    });
    canvasRef.current?.clearCanvas();
    setSolved(true);
  };

  const getJjimList = async () => {
    const profile = await getDoc(doc(db, "users", String(userUID)));
    if (profile.exists()) {
      setJjimArray(profile.data().jjimlist);
    }
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
        width: `100%`,
        backgroundColor: "#FCF6F5",
        overflow: "scroll",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          width: "100%",
          height: "75%",
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
          canvasColor="white"
          allowOnlyPointerType={pointer}
          backgroundImage={`https://storage.cloud.google.com/gildong-k-history/${
            pArray[currentNum]?.slice(0, -4) +
            "/" +
            pArray[currentNum]?.slice(-4, -2) +
            "/" +
            String(Number(pArray[currentNum]?.slice(-2)) - 1)
          }.png`}
          preserveBackgroundImageAspectRatio="xMidYMid meet"
        />
      </div>
      <div>
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
          disabled={currentNum === pArray.length}
          onClick={() => {
            handleClickNextButton();
          }}
          style={{ width: "20%", fontSize: "10%", marginLeft: "5px" }}
        >
          다음 문제
        </Button>
        <Button
          variant="contained"
          onClick={() => setIsDialogOpen(false)}
          style={{ width: "20%", fontSize: "10%", marginLeft: "5px" }}
        >
          나가기
        </Button>
      </div>
      <div>
        <Dialog
          open={solved}
          onClose={() => {
            setSolved(false);
            const newCurrentNum = currentNum + 1;
            if (newCurrentNum < pArray.length) {
              console.log(pArray, newCurrentNum);
              setCurrentNum(newCurrentNum);
              setStartTime(new Date().getTime());
              setSelected(0);
            } else {
              setIsDialogOpen(false);
            }
          }}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle>
            {`${
              pArray[currentNum].slice(0, -4) === "basic" ? "기본" : "심화"
            } ${pArray[currentNum].slice(-4, -2)}회 ${pArray[currentNum].slice(
              -2
            )}번 테스트 결과 : ${
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
                    <TableCell>해설</TableCell>
                    <TableCell>찜하기</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow
                    style={
                      selected !== answer ? { backgroundColor: "#fd7171" } : {}
                    }
                  >
                    <TableCell>
                      {pArray[currentNum]?.slice(-4, -2)}회{" "}
                      {pArray[currentNum]?.slice(-2)}번
                    </TableCell>
                    <TableCell>{selected}</TableCell>
                    <TableCell>{answer}</TableCell>
                    <TableCell
                      onClick={() => {
                        window.open(link, "_blank");
                      }}
                    >
                      link
                    </TableCell>
                    <TableCell>
                      <Button
                        onClick={() => {
                          const p = pArray[currentNum];
                          jjimArray?.indexOf(p) === -1
                            ? addJjimList(p)
                            : deleteJjimList(p);
                        }}
                      >
                        {jjimArray?.indexOf(pArray[currentNum]) === -1 ? (
                          <StarBorderIcon />
                        ) : (
                          <StarIcon />
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
export default SpecificSolve;
