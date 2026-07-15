import React from "react";

const CustomButton = ({ functie, classStyle, text, textStyle, disabled }) => {
  return (
    <button
      style={{
        cursor: "pointer",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
      disabled={!disabled}
      onClick={functie}
      className={classStyle}
    >
      <span style={{ fontSize: 50 }}>{text}</span>
    </button>
  );
};

export default CustomButton;
