import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getOverviewStats, getDailyStats, getClassDistribution } from '../services/api';

export const fetchOverview = createAsyncThunk('statistics/overview', async () => {
  return await getOverviewStats();
});

export const fetchDaily = createAsyncThunk('statistics/daily', async () => {
  return await getDailyStats();
});

export const fetchClassDistribution = createAsyncThunk('statistics/classes', async () => {
  return await getClassDistribution();
});

const statisticsSlice = createSlice({
  name: 'statistics',
  initialState: { overview: {}, daily: [], classes: {}, loading: false },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchOverview.fulfilled, (state, action) => {
        state.overview = action.payload;
      })
      .addCase(fetchDaily.fulfilled, (state, action) => {
        state.daily = action.payload;
      })
      .addCase(fetchClassDistribution.fulfilled, (state, action) => {
        state.classes = action.payload;
      });
  },
});

export default statisticsSlice.reducer;
