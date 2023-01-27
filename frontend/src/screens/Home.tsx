function Home() {
  return (
    <div style={{ textAlign: "center" }}>
      <img
        className="logo-img"
        src="gildong-home.png"
        alt="네이버 부스트캠프 AI Tech"
        style={{ maxHeight: "50vh", maxWidth: "100%" }}
      />
      <p>
        한국사 문제를 사용자에게 편리하게 제공하여 어디에서나 문제를 풀 수 있고
        성적을 확인할 수 있게 제공합니다.
      </p>
      <p>
        추후 사용자의 풀이 정보를 바탕으로 인공지능 기반의 문제 추천 서비스를
        제공하고자 합니다.
      </p>
      <p>2023.01.27 업데이트 내역 : AI 분석 항목 추가</p>
    </div>
  );
}

export default Home;
