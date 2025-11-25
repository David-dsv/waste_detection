import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getAlerts } from '../services/api';

export const fetchAlerts = createAsyncThunk('alerts/fetch', async (params) => {
  return await getAlerts(params);
});

const alertsSlice = createSlice({
  name: 'alerts',
  initialState: { list: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlerts.pending, (state) => { state.loading = true; })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload.alerts;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export default alertsSlice.reducer;
