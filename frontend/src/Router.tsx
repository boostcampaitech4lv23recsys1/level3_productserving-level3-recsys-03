import { createBrowserRouter, Routes, Route } from "react-router-dom";
import About from "./screens/About";
import Home from "./screens/Home";
import Root from "./Root";
import Community from "./screens/Community";
import QRef from "./screens/QRef";
import Solve from "./screens/FullTestSolve";
import Profile from "./screens/Profile";
import Auth from "./Auth";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      {
        path: "",
        element: <Home />,
      },
      {
        path: "about",
        element: <About />,
      },
      {
        path: "qref",
        element: <QRef />,
      },
      {
        path: "solve",
        element: <Solve />,
      },
      {
        path: "profile",
        element: <Profile />,
      },
      {
        path: "auth",
        element: <Auth />,
      },
    ],
  },
]);

export default router;
