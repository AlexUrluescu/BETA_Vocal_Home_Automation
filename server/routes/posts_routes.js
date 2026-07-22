import { Router } from "express";
import {
  getDataSenzors,
  getHeatingStatus,
  getTreshold,
  getSenzor,
  getTestServer,
} from "../controllers/post.controllers.js";

const router = Router();

router.get("/datasenzors", getDataSenzors);
router.get("/status", getHeatingStatus);
router.get("/treshold", getTreshold);
router.get("/senzor", getSenzor);
router.get("/test-server", getTestServer);

export default router;
