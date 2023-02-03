import { Link } from "react-router-dom";
import BottomNavigation from "@mui/material/BottomNavigation";
import BottomNavigationAction from "@mui/material/BottomNavigationAction";
import QuizOutlinedIcon from "@mui/icons-material/QuizOutlined";
import AccountCircleOutlinedIcon from "@mui/icons-material/AccountCircleOutlined";
import ForumOutlinedIcon from "@mui/icons-material/ForumOutlined";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import { useState } from "react";

import PsychologyAltOutlinedIcon from "@mui/icons-material/PsychologyAltOutlined";

function Footer() {
  const [value, setValue] = useState(window.location.pathname);
  return (
    <footer>
      <BottomNavigation
        showLabels
        value={value}
        onChange={(event, newValue) => {
          setValue(newValue);
        }}
        style={{
          position: "fixed",
          bottom: "0px",
          left: "0px",
          width: "100%",
          height: "10%",
          backgroundColor: "#D5BCA2",
        }}
      >
        <BottomNavigationAction
          component={Link}
          to="/"
          label="홈"
          icon={<HomeOutlinedIcon />}
        />
        <BottomNavigationAction
          component={Link}
          to="/qref"
          label="문제 풀기"
          icon={<QuizOutlinedIcon />}
        />
        <BottomNavigationAction
          component={Link}
          to="/profile"
          label="프로필"
          icon={<AccountCircleOutlinedIcon />}
        />
        <BottomNavigationAction
          component={Link}
          to="/ai"
          label="AI 분석"
          icon={<PsychologyAltOutlinedIcon />}
        />
      </BottomNavigation>
    </footer>
  );
}

export default Footer;
