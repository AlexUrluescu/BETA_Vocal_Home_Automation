import React from "react";

const InfoMessage = ({
  showTresholdUpdateMessage,
  classStyle,
  textStyle,
  text,
}) => {
  return (
    <div className={classStyle}>
      {showTresholdUpdateMessage === true ? (
        <p className={textStyle}>{text}</p>
      ) : (
        <p> </p>
      )}
    </div>
  );
};

export default InfoMessage;
