import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  Stack,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { roundOfExamAtom, diffOfExamAtom } from "../atoms";

function Fulltest() {
  const diffOfExam = useRecoilValue(diffOfExamAtom);
  const setDiffOfExam = useSetRecoilState(diffOfExamAtom);
  const roundOfExam = useRecoilValue(roundOfExamAtom);
  const setRoundOfExam = useSetRecoilState(roundOfExamAtom);
  const handleDifficultyChange = (event: SelectChangeEvent) => {
    setDiffOfExam(event.target.value);
  };
  const handleRoundChange = (event: SelectChangeEvent) => {
    setRoundOfExam(event.target.value);
  };
  const [rounds, setRounds] = useState<Array<string>>([])
  const diffs = ["basic", "advanced"];
  useEffect(()=>{
    console.log(diffOfExam)
    if(diffOfExam==='basic'){
      setRounds(['47','48','49','50','51','52','54','55','57','58','60','61'])
    }
    else if(diffOfExam==='advanced'){
      setRounds(['47','48','49','50','51','52','53','54','55','56','57','58','59','60','61','62'])
    }
  }, [diffOfExam])
  return (
    <div style={{ display: "flex", flexDirection: "column", padding: "5vh", alignItems:"center" }}>
      <Box sx={{ minWidth: 120, maxWidth: "50%", alignItems: "center" }}>
        <Stack direction="column" spacing={2}>
          <FormControl fullWidth>
            <InputLabel id="diff-select-label">난이도</InputLabel>
            <Select
              labelId="diff-select-label"
              id="diff-select"
              value={diffOfExam}
              label="난이도"
              onChange={handleDifficultyChange}
            >
              {diffs.map((difficulty) => (
                <MenuItem value={difficulty}>{difficulty==="basic"?"기본":"심화"}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth>
            <InputLabel id="round-select-label">시행 회차</InputLabel>
            <Select
              labelId="round-select-label"
              id="round-select"
              value={roundOfExam}
              label="시행 회차"
              onChange={handleRoundChange}
            >
              {rounds.map((round) => (
                <MenuItem value={round}>{round}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </Box>
    </div>
  );
}

export default Fulltest;
