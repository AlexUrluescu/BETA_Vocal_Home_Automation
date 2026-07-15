import React from "react";

const Title = ({ title, classStyle }) => {
  return (
    <div>
      <h1 className={classStyle}>{title}</h1>
    </div>
  );
};

export default Title;
