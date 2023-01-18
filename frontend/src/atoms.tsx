import { atom } from "recoil";

export const userUIDAtom = atom({
  key: "userUDIAtom",
  default: {},
});

export const isLoggedInAtom = atom({
  key: "isLoggedIn",
  default: false,
});

export const diffOfExamAtom = atom({
  key: "diffOfExam",
  default: "",
});

export const roundOfExamAtom = atom({
  key: "roundOfExam",
  default: "",
});

export const sectionAtom = atom({
  key: "sction",
  default: 1,
});

export const subSectionAtom = atom({
  key: "subSection",
  default: 1,
});

export const isSolvingAtom = atom({
  key: "isSolving",
  default: false,
});

export const isFullTestAtom = atom({
  key: "isFullTest",
  default: true,
});

export const isDialogOpenAtom = atom({
  key: "isDialogOpen",
  default: false
})