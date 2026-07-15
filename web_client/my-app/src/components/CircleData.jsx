import React from "react";

const CircleData = ({ data, classStyle, text, textStyle }) => {
  return (
    <div className={classStyle}>
      <h2 className="text-7xl ml-4">
        {data}
        <sup className={textStyle}>{text}</sup>
      </h2>
    </div>
  );
};

export default CircleData;
