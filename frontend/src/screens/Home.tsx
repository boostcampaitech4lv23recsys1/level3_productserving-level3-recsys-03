function Home() {
  return (
    <div style={{ textAlign: "center" }}>
      <img
        className="logo-img"
        src="gildong-home.png"
        alt="네이버 부스트캠프 AI Tech"
        style={{  maxHeight:"50vh", maxWidth:"100%" }}
      />
      <p>
        길동국사.com은 네이버 부스트캠프 AI Tech 4기 3조 Five-Guys 의 팀
        프로젝트 사이트입니다.
      </p>
      <p>
        한국사 문제를 사용자에게 편리하게 제공하여 어디에서나 문제를 풀 수 있고
        성적을 확인하실 수 있게 제공합니다.
      </p>
      <p>
        추후 사용자의 풀이 정보를 바탕으로 인공지능 기반의 문제 추천 서비스를
        제공하려고 합니다.
      </p>
      <p>문제 많이 풀어주세요! 여러분의 문제 풀이가 저희에게 도움이 됩니다.</p>
      <p>문제를 푸시면 매주 추첨을 통해서 🐓치킨 기프티콘 3장을 드립니다.</p>
    </div>
  );
}

export default Home;
