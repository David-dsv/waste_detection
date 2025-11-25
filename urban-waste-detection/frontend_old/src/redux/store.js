/**
 * Redux Store avec Redux Toolkit.
 */

import { configureStore } from '@reduxjs/toolkit';
import detectionsReducer from './detectionsSlice';
import alertsReducer from './alertsSlice';
import statisticsReducer from './statisticsSlice';

export const store = configureStore({
  reducer: {
    detections: detectionsReducer,
    alerts: alertsReducer,
    statistics: statisticsReducer,
  },
});

export default store;
